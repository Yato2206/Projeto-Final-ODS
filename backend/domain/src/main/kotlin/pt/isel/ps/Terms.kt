package pt.isel.ps

data class Terms(
    val id: Int,
    val odsId: Int,
    val name: String,
    val origin: String,
) {
    init {
        require(id >= 0) { "Terms ID must be greater than or equal to zero." }
        require(odsId >= 0) { "ODS ID must be greater than or equal to zero." }
        require(name.isNotBlank()) { "Name must not be blank." }
        require(origin.isNotBlank()) { "Origin must not be blank." }
    }
}