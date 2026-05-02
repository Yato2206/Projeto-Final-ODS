package pt.isel.ps.mem

import pt.isel.ps.Document
import pt.isel.ps.RepositoryDocument

class RepositoryDocumentInMem: RepositoryDocument {
    private val documents = mutableListOf(
        Document(id = 0, name = "Document 0", origin = "Origin0", filePath = "filePath0"),
        Document(id = 1, name = "Document 1", origin = "Origin1", filePath = "filePath1"),
        Document(id = 2, name = "Document 0", origin = "Origin0", filePath = "filePath2"),
    )

    override fun createDocument(name: String, origin: String, filePath: String): Document =
        Document(id = documents.size,name = name, origin = origin, filePath = filePath).also{ documents.add(it) }

    override fun getDocumentsByName(name: String): List<Document> =
        documents.filter { it.name == name }

    override fun getOrigin(docId: Int): String? = documents.find { it.id == docId }?.origin

    override fun getFilepath(docId: Int): String? = documents.find { it.id == docId }?.filePath

    override fun getById(id: Int): Document? = documents.find { it.id == id }

    override fun getAll(): List<Document> = documents.toList()

    override fun save(entity: Document) {
        documents.removeIf { it.id == entity.id }
        documents.add(entity)
    }

    override fun deleteById(id: Int): Boolean = documents.removeIf { it.id == id }

    override fun clear() = documents.clear()

}