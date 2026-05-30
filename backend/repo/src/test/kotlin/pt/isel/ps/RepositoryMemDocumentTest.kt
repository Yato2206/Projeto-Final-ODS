package pt.isel.ps

import org.junit.jupiter.api.BeforeEach
import pt.isel.ps.mem.RepositoryDocumentInMem
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNull

class RepositoryMemDocumentTest {
    private lateinit var repo: RepositoryDocument

    @BeforeEach
    fun setUp() {
        repo = RepositoryDocumentInMem()
    }

    @Test
    fun `create a Document`() {
        val create = repo.createDocument("Teste", "Origin1", "filePath1")
        assertEquals(Document(id = 3, name = "Teste", origin = "Origin1", filePath = "filePath1"), create)
    }

    @Test
    fun `get a Document by ID`() {
        val found = repo.getById(0)
        assertEquals(Document(0, "Document 0", "Origin0", "filePath0"), found)
    }

    @Test
    fun `get an inexistent Document by ID`() {
        val found = repo.getById(5)
        assertNull(found)
    }

    @Test
    fun `getDocumentsByName returns correct Documents`() {
        val found = repo.getDocumentsByName("Document 0")
        assertEquals(2, found.size)
        assertEquals(listOf<Document>(
            Document(0, "Document 0", "Origin0", "filePath0"),
            Document(2, "Document 0", "Origin0", "filePath2")
        ), found)
    }

    @Test
    fun `getDocumentsByName returns inexistent Documents (empty)`() {
        val found = repo.getDocumentsByName("Inexistent Document")
        assertEquals(emptyList<Document>(), found)
    }

    @Test
    fun `getAll returns all Documents`() {
        val found = repo.getAll()
        val documentList = listOf(
            Document(id = 0, name = "Document 0", origin = "Origin0", filePath = "filePath0"),
            Document(id = 1, name = "Document 1", origin = "Origin1", filePath = "filePath1"),
            Document(id = 2, name = "Document 0", origin = "Origin0", filePath = "filePath2")
        )
        assertEquals(documentList.size, found.size)
        assertEquals(documentList, found)
    }

    @Test
    fun `getOrigin returns the origin of a given Document ID`() {
        val found = repo.getOrigin(0)
        assertEquals("Origin0", found)
    }

    @Test
    fun `getOrigin returns null because inexistent Document ID`() {
        val found = repo.getOrigin(5)
        assertNull(found)
    }

    @Test
    fun `getFilePath returns the file path of a given Document ID`() {
        val found = repo.getFilepath(0)
        assertEquals("filePath0", found)
    }

    @Test
    fun `getFilePath returns null because inexistent Document ID`() {
        val found = repo.getFilepath(5)
        assertNull(found)
    }

    @Test
    fun `save updates an existing Document`() {
        val updatedDocument = Document(0, "Updated Document", "Updated Origin", "Updated filePath")
        repo.save(updatedDocument)
        val found = repo.getById(0)
        assertEquals(updatedDocument, found)
    }

    @Test
    fun `deleteById removes an existing Document`() {
        val found = repo.getById(0)
        assertEquals(Document(0, "Document 0", "Origin0", "filePath0"), found)
        val deleted = repo.deleteById(0)
        assertEquals(true, deleted)
        val shouldBeNull = repo.getById(0)
        assertNull(shouldBeNull)
    }

    @Test
    fun `deleteById returns null`() {
        val deleted = repo.deleteById(5)
        assertEquals(false, deleted)
    }

    @Test
    fun `clear puts the Document list empty`() {
        val cleared = repo.clear()
        assertEquals(Unit, cleared)
        val foundDocument = repo.getById(0)
        assertNull(foundDocument)
        val foundList = repo.getAll()
        assertEquals(emptyList<Document>(), foundList)
        assertEquals(0, foundList.size)
    }
}