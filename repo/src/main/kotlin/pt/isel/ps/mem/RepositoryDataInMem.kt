package pt.isel.ps.mem

import pt.isel.ps.Data
import pt.isel.ps.DataType
import pt.isel.ps.Ods
import pt.isel.ps.RepositoryData
import java.time.LocalDateTime

class RepositoryDataInMem: RepositoryData {

    private val odsRepo = RepositoryOdsInMem()

    // Deterministic timestamp so tests don't depend on the current clock.
    private val fixedDateChecked: LocalDateTime = LocalDateTime.of(2026, 3, 25, 0, 0)

    private val data = mutableListOf<Data>(
        Data(id = 0, odsId = listOf(1), type = DataType.ARTISTICO, origin = "Origin1", dateChecked = fixedDateChecked),
        Data(id = 1, odsId = listOf(3, 16), type = DataType.CIENTIFICO, origin = "Origin2", dateChecked = fixedDateChecked),
        Data(id = 2, odsId = listOf(5, 6, 7), type = DataType.ACAO_NA_SOCIEDADE, origin = "Origin1", dateChecked = fixedDateChecked),
        Data(id = 3, odsId = listOf(), type = DataType.ARTISTICO, origin = "Origin4", dateChecked = fixedDateChecked),
        Data(id = 4, odsId = listOf(4, 8, 11), type = DataType.ENSINO, origin = "Origin5", dateChecked = fixedDateChecked),
    )

    override fun getById(id: Int): Data? = data.find { it.id == id }

    override fun getAll(): List<Data> = data.toList()

    override fun save(entity: Data) {
        data.removeIf { it.id == entity.id }
        data.add(entity)
    }

    override fun createData(origin: String, dateChecked: LocalDateTime): Data = Data(id = data.size, origin = origin, dateChecked = dateChecked).also { data.add(it) }

    override fun getOds(dataId: Int): List<Ods> =
        getById(dataId)
            ?.odsId
            ?.mapNotNull { odsRepo.getById(it) }
            ?: emptyList()

    override fun getOrigin(dataId: Int): String? = data.find { it.id == dataId }?.origin

    override fun getType(dataId: Int): DataType? = data.find { it.id == dataId }?.type

    override fun getDateChecked(dataId: Int): LocalDateTime? = data.find { it.id == dataId }?.dateChecked

    override fun deleteById(id: Int): Boolean = data.removeIf { it.id == id }

    override fun clear() = data.clear()
}