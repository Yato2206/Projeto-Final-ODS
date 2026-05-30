package pt.isel.ps

import org.example.Either
import org.example.failure
import org.example.success
import org.springframework.stereotype.Component
import javax.print.Doc

sealed class DocumentError {
    data object DocumentAlreadyExists : DocumentError()
    data object NotFound : DocumentError()
}

@Component
class DocumentServices(
    private val trxManager: TransactionManager,
) {
    fun createDocument(name: String, origin: String, filePath: String): Either<DocumentError, Document> {
        return trxManager.run {
            val documents = repoDocument.getDocumentsByName(name)
            if (documents.find { it.name == name && it.origin == origin && it.filePath == filePath } != null) {
                return@run failure(DocumentError.DocumentAlreadyExists)
            }
            val document = repoDocument.createDocument(name, origin, filePath)
            success(document)
        }
    }

    fun getAllDocuments(): List<Document> = trxManager.run { repoDocument.getAll() }

    fun getDocumentById(docId: Int): Either<DocumentError, Document> {
        return trxManager.run {
            val document = repoDocument.getById(docId) ?: return@run failure(DocumentError.NotFound)
            success(document)
        }
    }

    fun getDocumentOrigin(docId: Int): Either<DocumentError, String> {
        return trxManager.run {
            val origin = repoDocument.getOrigin(docId) ?: return@run failure(DocumentError.NotFound)
            success(origin)
        }
    }

    fun getDocumentFilePath(docId: Int): Either<DocumentError, String> {
        return trxManager.run {
            val filePath = repoDocument.getFilepath(docId) ?: return@run failure(DocumentError.NotFound)
            success(filePath)
        }
    }

    fun deleteDocument(docId: Int): Either<DocumentError, Boolean> {
        return trxManager.run {
            repoDocument.getById(docId) ?: return@run failure(DocumentError.NotFound)
            success(repoDocument.deleteById(docId))
        }
    }

}