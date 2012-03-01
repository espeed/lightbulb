// 
// Copyright 2012 James Thornton (http://jamesthornton.com)
// BSD License (see LICENSE for details)
//


def save_blog_entry(entry_bundle, author_id, topic_bundles) {

  def create_indexed_vertex = { final Map bundle ->
    data = bundle['data']
    index_name = bundle['index_name']
    keys = bundle['keys']
    vertex = g.addVertex()
    index = g.idx(index_name)
    for (property in data) {
      if (property.value == null) continue;
      vertex.setProperty(property.key, property.value)
      if (keys == null || keys.contains(property.key))
	index.put(property.key, String.valueOf(property.value), vertex)
    }
    return vertex
  }

  def update_indexed_vertex = { final Vertex vertex, final Map bundle ->
    data = bundle['data']
    index_name = bundle['index_name']
    keys = bundle['keys']
    index = g.idx(index_name);
    // remove vertex from index
    for (String key in vertex.getPropertyKeys()) {
      if (keys == null || keys.contains(key)) {
	value = vertex.getProperty(key);
	index.remove(key, String.valueOf(value), vertex);
      }
    }
    // update element properties
    ElementHelper.removeProperties([vertex]);
    ElementHelper.setProperties(vertex, data);
    // add vertex to index
    for (entry in data.entrySet()) {
      if (entry.value == null) continue;
      if (keys == null || keys.contains(entry.key))
	index.put(entry.key,String.valueOf(entry.value),vertex);
    }    
    return vertex;
  }

  def create_or_update_vertex = { final Map bundle, final String index_key ->
    index_name = bundle['index_name']
    index_value = bundle['data'][index_key]
    vertices = g.idx(index_name).get(index_key, index_value).toList()
    if (vertices.size() == 0) {
      vertex = create_indexed_vertex(bundle)
    } else {
      assert vertices.size() == 1
      vertex = update_indexed_vertex(vertices[0], bundle)
    }
    return vertex      
  }

  def get_or_create_vertex = { final Map bundle, final String index_key ->
    index_name = bundle['index_name']
    index_value = bundle['data'][index_key]
    vertices = g.idx(index_name).get(index_key, index_value).toList()
    if (vertices.size() == 0) {
      vertex = create_indexed_vertex(bundle)
    } else {
      assert vertices.size() == 1
      vertex = vertices[0]
    }
    return vertex      
  }

  def transaction = { final Closure closure ->
    g.setMaxBufferSize(0);
    g.startTransaction();
    try {
      results = closure();
      g.stopTransaction(TransactionalGraph.Conclusion.SUCCESS);
      return results; 
    } catch (e) {
      g.stopTransaction(TransactionalGraph.Conclusion.FAILURE);
      return e;
    }
  }

  def save_blog_entry = { 
    entry = create_or_update_vertex(entry_bundle, "docid");
    author = g.v(author_id)
    found = entry.out("author").filter{it == author}.count()
    if (!found) { g.addEdge(entry, author, "author"); }
    for (topic_bundle in topic_bundles)  {
      topic = get_or_create_vertex(topic_bundle, "name");
      // TODO: remove topics if needed
      found = entry.out("tagged").filter{it == topic}.count()
      if (!found) { g.addEdge(entry, topic, "tagged"); }
    }
    return entry;
  }
  
  return transaction(save_blog_entry);
}


