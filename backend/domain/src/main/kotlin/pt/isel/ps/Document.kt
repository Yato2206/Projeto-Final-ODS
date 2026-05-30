package pt.isel.ps

data class Document(
    val id: Int,
    val name: String,
    val origin: String,
    val filePath: String
) {
    init {
        require(id >= 0) { "Document ID must be greater than or equal to zero." }
        require(name.isNotBlank()) { "Name must not be blank" }
        require(origin.isNotBlank()) { "Origin must not be blank" }
        require(filePath.isNotBlank()) { "File path must not be blank" }
    }
}