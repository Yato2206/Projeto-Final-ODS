package pt.isel.ps

import org.example.Failure
import org.example.Success
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.test.annotation.DirtiesContext
import org.springframework.test.context.junit.jupiter.SpringJUnitConfig
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertIs

@SpringJUnitConfig(TestConfig::class)
@DirtiesContext(classMode = DirtiesContext.ClassMode.AFTER_EACH_TEST_METHOD)
class TestAnalysisServices {
    @Autowired
    private lateinit var service: AnalysisServices

    @Test
    fun `CreateAnalysis creates new Analysis`() {
        val analysis = service.createAnalysis(
            docId = 0,
            filePath = "filepath1"
        )
        assertEquals(5, analysis.id)
        assertEquals(0, analysis.docId)
        assertEquals("filepath1", analysis.filePath)
    }

    @Test
    fun `getAllAnalysis returns all Analysis`() {
        val analysis = service.getAllAnalysis()
        assertEquals(5, analysis.size)
        assertEquals(Analysis(id = 0, docId = 0, filePath = "filePath0"), analysis[0])
        assertEquals(Analysis(id = 1, docId = 0, filePath = "filePath1"), analysis[1])
    }

    @Test
    fun `getAnalysisById returns a Analysis`() {
        val analysis = service.getAnalysisById(1)
        assertIs<Success<Analysis>>(analysis)
        assertEquals(1, analysis.value.id)
        assertEquals(0, analysis.value.docId)
        assertEquals("filePath1", analysis.value.filePath)
    }

    @Test
    fun `getAnalysisById returns error because Analysis inexistent`() {
        val getAnalysisById = service.getAnalysisById(100)
        assertIs<Failure<AnalysisError.NotFound>>(getAnalysisById)
    }

    @Test
    fun `getDocument returns a Document`() {
        val document = service.getDocument(1)
        assertIs<Success<Document>>(document)
        assertEquals(0, document.value.id)
        assertEquals("Document 0", document.value.name)
        assertEquals("Origin0", document.value.origin)
        assertEquals("filePath0", document.value.filePath)
    }

    @Test
    fun `getDocument returns error because Document inexistent`() {
        val getDocument = service.getDocument(100)
        assertIs<Failure<AnalysisError.NotFound>>(getDocument)
    }

    @Test
    fun `getFilepath returns a filepath`() {
        val filepath = service.getFilepath(1)
        assertIs<Success<String>>(filepath)
        assertEquals("filePath1", filepath.value)
    }

    @Test
    fun `getFilepath returns error because Analysis inexistent`() {
        val filepath = service.getFilepath(100)
        assertIs<Failure<AnalysisError.NotFound>>(filepath)
    }

    @Test
    fun `deleteAnalysis deletes a analysis`() {
        val deleted = service.deleteAnalysis(2)
        assertIs<Success<Boolean>>(deleted)
        val deletedValue = deleted.value
        assertEquals(true, deletedValue)
    }

    @Test
    fun `deleteAnalysis fails to delete a analysis`() {
        val deleted = service.deleteAnalysis(7)
        assertIs<Failure<AnalysisError.NotFound>>(deleted)
    }

}