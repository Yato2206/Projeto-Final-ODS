package pt.isel.ps

import org.junit.jupiter.api.BeforeEach
import pt.isel.ps.mem.RepositoryAnalysisInMem
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNull

class RepositoryMemAnalysisTest {
    private lateinit var repo: RepositoryAnalysis

    @BeforeEach
    fun setUp() {
        repo = RepositoryAnalysisInMem()
    }

    @Test
    fun `getById returns the correct ID`() {
        val analysis = repo.getById(1)
        assertEquals(Analysis(id = 1, docId = 0, filePath = "filePath1"), analysis)
    }

    @Test
    fun `getAll returns all Analysis`() {
        val found = repo.getAll()
        val analysisList = listOf(
            Analysis(id = 0, docId = 0, filePath = "filePath0"),
            Analysis(id = 1, docId = 0, filePath = "filePath1"),
            Analysis(id = 2, docId = 1, filePath = "filePath2"),
            Analysis(id = 3, docId = 1, filePath = "filePath3"),
            Analysis(id = 4, docId = 2, filePath = "filePath4")
        )
        assertEquals(analysisList.size, found.size)
        assertEquals(analysisList, found)
    }

    @Test
    fun `save updates an existing Analysis`() {
        val updatedAnalysis = Analysis(0, 0, "UpdatedFilePath")
        repo.save(updatedAnalysis)
        val found = repo.getById(0)
        assertEquals(updatedAnalysis, found)
    }

    @Test
    fun `create an Analysis`() {
        val create = repo.createAnalysis(1, "TesFilePath")
        assertEquals(Analysis(5, 1, "TesFilePath"), create)
    }

    @Test
    fun `getDocument gets the correct Document`() {
        val doc = repo.getDocument(1)
        assertEquals(Document(id = 0, name = "Document 0", origin = "Origin0", filePath = "filePath0"), doc)
    }

    @Test
    fun `getFilePath gets the correct FilePath`() {
        val filepath = repo.getFilepath(1)
        assertEquals("filePath1", filepath)
    }

    @Test
    fun `deleteById removes an existing Analysis`() {
        val found = repo.getById(0)
        assertEquals(Analysis(0, 0, "filePath0"), found)
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
    fun `clear puts the Analysis list empty`() {
        val cleared = repo.clear()
        assertEquals(Unit, cleared)
        val foundAnalysis = repo.getById(0)
        assertNull(foundAnalysis)
        val foundList = repo.getAll()
        assertEquals(emptyList<Analysis>(), foundList)
        assertEquals(0, foundList.size)
    }
}