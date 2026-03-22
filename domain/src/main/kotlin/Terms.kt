data class Terms(
    val id: Int,
    val odsId: List<Int>,
    val name: String,
    val origin: String,
) {
    init {
        require(id >= 0) { "Terms ID must be greater than or equal to zero." }
        require(odsId.isNotEmpty()) { "ODS ID list must not be empty." }
        require(name.isNotBlank()) { "Name must not be blank." }
        require(origin.isNotBlank()) { "Origin must not be blank." }
    }
}