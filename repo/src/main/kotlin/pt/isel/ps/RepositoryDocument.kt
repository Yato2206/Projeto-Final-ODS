package pt.isel.ps

interface RepositoryDocument: Repository<Document> {
    fun createDocument(name: String, origin: String, filePath: String): Document
    fun getDocumentsByName(name: String): List<Document>
    fun getOrigin(docId: Int): String?
    fun getFilepath(docId: Int): String?
}