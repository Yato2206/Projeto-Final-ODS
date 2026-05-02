package pt.isel.ps

data class Analysis(
    val id: Int,
    val docId: Int,
    val filePath: String,
) {
    init {
        require(id >= 0) { "Analysis ID must be greater than or equal to zero." }
        require(docId >= 0) { "Document ID must be greater than or equal to zero." }
        require(filePath.isNotBlank()) { "File path must not be blank" }
    }
}