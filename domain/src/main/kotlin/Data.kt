import java.time.LocalDateTime

data class Data(
    val id: Int,
    val odsId: List<Int>? = null,
    val type: DataType = DataType.UNDEFINED,
    val origin: String,
    val dateChecked: LocalDateTime,
) {
    init {
        require(id >= 0) { "Data ID must be greater than or equal to zero." }
        require(origin.isNotBlank()) { "Origin must not be blank" }
        require(dateChecked <= LocalDateTime.now()) { "Date checked cannot be in the future." }
    }
}