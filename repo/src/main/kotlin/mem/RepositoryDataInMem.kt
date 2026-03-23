package mem

import Data
import DataType
import Ods
import RepositoryData
import java.time.LocalDateTime

class RepositoryDataInMem: RepositoryData {

    private val odsRepo = RepositoryOdsInMem()

    private val data = mutableListOf<Data>(
        Data(id = 1, odsId = listOf(1), type = DataType.ARTISTICO, origin = "Origin1", dateChecked = LocalDateTime.now()),
        Data(id = 2, odsId = listOf(3, 17), type = DataType.CIENTIFICO, origin = "Origin2", dateChecked = LocalDateTime.now()),
        Data(id = 3, odsId = listOf(5, 6, 7), type = DataType.ACAO_NA_SOCIEDADE, origin = "Origin1", dateChecked = LocalDateTime.now()),
        Data(id = 4, odsId = listOf(6, 13), type = DataType.ARTISTICO, origin = "Origin4", dateChecked = LocalDateTime.now()),
        Data(id = 5, odsId = listOf(4, 8, 11), type = DataType.ENSINO, origin = "Origin5", dateChecked = LocalDateTime.now()),
    )

    override fun getById(id: Int): Data? = data.find { it.id == id }

    override fun getAll(): List<Data> = data.toList()

    override fun save(entity: Data) {
        data.removeIf { it.id == entity.id }
        data.add(entity)
    }

    override fun getOds(data: Data): List<Ods>? =
        data.odsId?.mapNotNull { id -> odsRepo.getById(id) }

    override fun getOrigin(dataId: Int): String = data.first { it.id == dataId }.origin

    override fun getType(dataId: Int): DataType = data.first { it.id == dataId }.type

    override fun getDateChecked(dataId: Int): LocalDateTime = data.first { it.id == dataId }.dateChecked

    override fun deleteById(id: Int): Boolean = data.removeIf { it.id == id }

    override fun clear() = data.clear()
}