package pt.isel.ps

import java.time.LocalDateTime

interface RepositoryData: Repository<Data> {
    fun createData(origin: String, dateChecked: LocalDateTime): Data
    fun getOds(dataId: Int): List<Ods>
    fun getOrigin(dataId: Int): String?
    fun getType(dataId: Int): DataType?
    fun getDateChecked(dataId: Int): LocalDateTime?
}