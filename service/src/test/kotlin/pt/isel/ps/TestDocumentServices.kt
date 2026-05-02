package pt.isel.ps

import org.example.Failure
import org.example.Success
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.test.annotation.DirtiesContext
import org.springframework.test.context.junit.jupiter.SpringJUnitConfig
import kotlin.test.assertEquals
import kotlin.test.assertIs
import kotlin.test.assertNotEquals

@SpringJUnitConfig(TestConfig::class)
@DirtiesContext(classMode = DirtiesContext.ClassMode.AFTER_EACH_TEST_METHOD)
class TestDocumentServices {
    @Autowired
    private lateinit var service: DocumentServices

    @Test
    fun `createDocument stores Document`() {
        val document = service.createDocument("Doc1", "Newsletter", "file1")
        assertIs<Success<Document>>(document)
        assertEquals("Doc1", document.value.name)
        assertEquals("Newsletter", document.value.origin)
        assertEquals("file1", document.value.filePath)
        assertEquals(3, document.value.id)
    }

    @Test
    fun `createDocument returns error because document already exists`() {
        val document = service.createDocument("Document 0", "Origin0", "filePath0")
        assertIs<Failure<DocumentError.DocumentAlreadyExists>>(document)
    }

    @Test
    fun `getAllDocument returns all Document`() {
        val documentList = service.getAllDocuments()
        assertEquals(3, documentList.size)
        assertEquals("Document 0", documentList[0].name)
        assertEquals("Document 1", documentList[1].name)
        assertEquals("Document 0", documentList[2].name)
    }

    @Test
    fun `getDocumentById returns Document`() {
        val document = service.getDocumentById(0)
        assertIs<Success<Document>>(document)
        assertEquals("Document 0", document.value.name)
        assertEquals("Origin0", document.value.origin)
        assertEquals("filePath0", document.value.filePath)
        assertEquals(0, document.value.id)
    }

    @Test
    fun `getDocumentById returns error because Document does not exist`() {
        val document = service.getDocumentById(100)
        assertIs<Failure<DocumentError.NotFound>>(document)
    }

    @Test
    fun `getDocumentOrigin returns the origin of the Document`() {
        val origin = service.getDocumentOrigin(0)
        assertIs<Success<String>>(origin)
        assertEquals("Origin0", origin.value)
    }

    @Test
    fun `getDocumentOrigin returns error because Document does not exist`() {
        val origin = service.getDocumentOrigin(100)
        assertIs<Failure<DocumentError.NotFound>>(origin)
    }

    @Test
    fun `getDocumentFilePath returns the file path of the Document`() {
        val filePath = service.getDocumentFilePath(0)
        assertIs<Success<String>>(filePath)
        assertEquals("filePath0", filePath.value)
    }

    @Test
    fun `getDocumentFilePath returns error because Document does not exist`() {
        val filePath = service.getDocumentFilePath(100)
        assertIs<Failure<DocumentError.NotFound>>(filePath)
    }

    @Test
    fun `deleteDocument deletes Document`() {
        val documentListBefore = service.getAllDocuments()
        assertEquals(3, documentListBefore.size)
        val documentDeleted = service.deleteDocument(0)
        assertIs<Success<Boolean>>(documentDeleted)
        val documentListAfter = service.getAllDocuments()
        assertNotEquals(documentListBefore.size, documentListAfter.size)
        assertEquals(2, documentListAfter.size)
    }

    @Test
    fun `deleteDocument returns error because Document does not exist`() {
        val documentDeleted = service.deleteDocument(100)
        assertIs<Failure<DocumentError.NotFound>>(documentDeleted)
    }
}