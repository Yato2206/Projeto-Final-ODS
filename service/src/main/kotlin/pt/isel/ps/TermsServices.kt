package pt.isel.ps

import org.example.Either
import org.example.failure
import org.example.success
import org.springframework.stereotype.Component

sealed class TermsError {
    data object TermAlreadyExists : TermsError()
    data object OdsNotFound : TermsError()
    data object NotFound : TermsError()
}

@Component
class TermsServices (
    private val trxManager: TransactionManager,
) {

    fun createTerm(name: String, odsId: Int, origin: String): Either<TermsError, Terms> {
        return trxManager.run {
            repoTerms.findByName(name)?.let {
                return@run failure(TermsError.TermAlreadyExists)
            }
            val term = repoTerms.createTerm(odsId, name, origin)
            success(term)
        }
    }

    fun getAllOdsTerms(odsId: Int): Either<TermsError, List<Terms>> {
        return trxManager.run {
            repoOds.getById(odsId)
                ?: return@run failure(TermsError.OdsNotFound)

            val terms = repoTerms.getAllOdsTerms(odsId)
            success(terms)
        }
    }

    fun deleteTerms(termsId: Int): Either<TermsError, Boolean> {
        return trxManager.run {
            repoOds.getById(termsId) ?: return@run failure(TermsError.NotFound)
            success(repoTerms.deleteById(termsId))
        }
    }

}