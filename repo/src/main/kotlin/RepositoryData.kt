import java.time.LocalDateTime

interface RepositoryData: Repository<Data> {
    fun getOds(data: Data): List<Ods>?
    fun getOrigin(data: Data): String
    fun getType(data: Data): DataType
    fun getDateChecked(data: Data): LocalDateTime
}