package pt.isel.ps.mem

import pt.isel.ps.Analysis
import pt.isel.ps.Document
import pt.isel.ps.RepositoryAnalysis

class RepositoryAnalysisInMem: RepositoryAnalysis {

    private val documentRepo = RepositoryDocumentInMem()

    private val analysis = mutableListOf<Analysis>(
        Analysis(id = 0, docId = 0, filePath = "filePath0"),
        Analysis(id = 1, docId = 0, filePath = "filePath1"),
        Analysis(id = 2, docId = 1, filePath = "filePath2"),
        Analysis(id = 3, docId = 1, filePath = "filePath3"),
        Analysis(id = 4, docId = 2, filePath = "filePath4"),
    )

    override fun getById(id: Int): Analysis? = analysis.find { it.id == id }

    override fun getAll(): List<Analysis> = analysis.toList()

    override fun save(entity: Analysis) {
        analysis.removeIf { it.id == entity.id }
        analysis.add(entity)
    }

    override fun createAnalysis(docId: Int, filePath: String): Analysis = Analysis(id = analysis.size, docId = docId, filePath = filePath).also{ analysis.add(it) }

    override fun getDocument(id: Int): Document? =
        getById(id)
            ?.docId
            ?.let { documentRepo.getById(it) }

    override fun getFilepath(analysisId: Int): String? = analysis.find { it.id == analysisId }?.filePath

    override fun deleteById(id: Int): Boolean = analysis.removeIf { it.id == id }

    override fun clear() = analysis.clear()
}