package pt.isel.ps

import org.example.Either
import org.example.failure
import org.example.success
import org.springframework.stereotype.Component
import java.time.LocalDateTime


sealed class DataError {
    //data object dataAlreadyExists : DataError()
    data object NotFound : DataError()
}

@Component
class DataServices(
    private val trxManager: TransactionManager,
) {
    fun createData(origin: String, dataChecked: LocalDateTime): Data {
        return trxManager.run { repoData.createData(origin, dataChecked) }
    }

    fun getAlldata(): List<Data> = trxManager.run { repoData.getAll() }

    fun getDataById(dataId: Int): Either<DataError, Data> {
        return trxManager.run {
            val data = repoData.getById(dataId) ?: return@run failure(DataError.NotFound)
            success(data)
        }
    }
    fun getOds(dataId: Int): Either<DataError, List<Ods>> {
        return trxManager.run {
            repoData.getById(dataId)
                ?: return@run failure(DataError.NotFound)
            val odsList = repoData.getOds(dataId)
            success(odsList)
        }
    }

    fun getOrigin(dataId: Int): Either<DataError, String> {
        return trxManager.run {
            val origin = repoData.getOrigin(dataId) ?: return@run failure(DataError.NotFound)
            success(origin)
        }
    }

    fun getType(dataId: Int): Either<DataError, DataType> {
        return trxManager.run {
            val type = repoData.getType(dataId) ?: return@run failure(DataError.NotFound)
            success(type)
        }
    }

    fun getDateChecked(dataId: Int): Either<DataError, LocalDateTime> {
        return trxManager.run {
            val dateChecked = repoData.getDateChecked(dataId) ?: return@run failure(DataError.NotFound)
            success(dateChecked)
        }
    }

    fun deleteData(dataId: Int): Either<DataError, Boolean> {
        return trxManager.run {
            repoData.getById(dataId) ?: return@run failure(DataError.NotFound)
            success(repoData.deleteById(dataId))
        }
    }

}