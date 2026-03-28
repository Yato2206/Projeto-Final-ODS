package pt.isel.ps

import org.example.Either
import org.example.failure
import org.example.success
import org.springframework.stereotype.Component

sealed class OdsError {
    data object OdsAlreadyExists : OdsError()
    data object NotFound : OdsError()
}

@Component
class OdsServices(
    private val trxManager: TransactionManager,
) {
    fun createOds(name: String): Either<OdsError, Ods> {
        return trxManager.run {
            repoOds.findByName(name)?.let {
                return@run failure(OdsError.OdsAlreadyExists)
            }
            val ods = repoOds.createOds(name)
            success(ods)
        }
    }

    fun getAllOds(): List<Ods> = trxManager.run { repoOds.getAll() }

    fun getOdsById(odsId: Int): Either<OdsError, Ods> {
        return trxManager.run {
            val ods = repoOds.getById(odsId) ?: return@run failure(OdsError.NotFound)
            success(ods)
        }
    }

    fun deleteOds(odsId: Int): Either<OdsError, Boolean> {
            return trxManager.run {
                repoOds.getById(odsId) ?: return@run failure(OdsError.NotFound)
                success(repoOds.deleteById(odsId))
            }
    }

}