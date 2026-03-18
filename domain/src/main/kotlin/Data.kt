import java.time.LocalDateTime

data class Data(
    val id: Int,
    val odsId: List<Ods>? = null,
    val type: DataType = DataType.UNDEFINED,
    val origin: String,
    val dateChecked: LocalDateTime,
)