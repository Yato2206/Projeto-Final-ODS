package pt.isel.ps

interface RepositoryAnalysis: Repository<Analysis> {
    fun createAnalysis(docId: Int, filePath: String): Analysis
    fun getDocument(id:Int) : Document?
    fun getFilepath(analysisId: Int): String?
}