data class Ods(
    val id: Int,
    val name: String,
) {
    init {
        require(id >= 0) { "ODS ID must be greater than or equal to zero." }
        require(name.isNotBlank()) { "Name must not be blank" }
    }
}