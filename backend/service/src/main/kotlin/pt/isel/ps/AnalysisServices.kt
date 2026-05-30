package pt.isel.ps

import org.example.Either
import org.example.failure
import org.example.success
import org.springframework.stereotype.Component

sealed class AnalysisError {
    data object NotFound : AnalysisError()
}

@Component
class AnalysisServices(
    private val trxManager: TransactionManager,
) {
    fun createAnalysis(docId: Int, filePath: String) : Analysis {
        return trxManager.run { repoAnalysis.createAnalysis(docId, filePath) }
    }

    fun getAnalysisById(analysisId: Int): Either<AnalysisError, Analysis> {
        return trxManager.run {
            val analysis = repoAnalysis.getById(analysisId) ?: return@run failure(AnalysisError.NotFound)
            success(analysis)
        }
    }

    fun getAllAnalysis(): List<Analysis> = trxManager.run { repoAnalysis.getAll() }

    fun getDocument(id:Int) : Either<AnalysisError, Document?> {
        return trxManager.run {
            val document = repoAnalysis.getDocument(id) ?: return@run failure(AnalysisError.NotFound)
            success(document)
        }
    }

    fun getFilepath(analysisId:Int) : Either<AnalysisError, String?> {
        return trxManager.run {
            val filepath = repoAnalysis.getFilepath(analysisId) ?: return@run failure(AnalysisError.NotFound)
            success(filepath)
        }
    }

    fun deleteAnalysis(analysisId: Int): Either<AnalysisError, Boolean> {
        return trxManager.run {
            repoData.getById(analysisId) ?: return@run failure(AnalysisError.NotFound)
            success(repoData.deleteById(analysisId))
        }
    }
}