package pt.isel.ps

import jdbc.pt.isel.ps.DatabaseConnection
import jdbc.pt.isel.ps.TransactionManagerJdbc
import org.junit.jupiter.api.Test
import kotlin.test.BeforeTest
import kotlin.test.assertEquals
import kotlin.test.assertNotEquals
import kotlin.test.assertNotNull
import kotlin.test.assertNull
import kotlin.test.assertFalse

class RepositoryJdbcDocumentTest {
    companion object {
        val trxManager = TransactionManagerJdbc()
        val con = DatabaseConnection.getConnection()
    }

    @BeforeTest
    fun setup() {
        val sql = "TRUNCATE dbo.document RESTART IDENTITY CASCADE;"
        con.prepareStatement(sql).use { stmt ->
            stmt.executeUpdate()
        }
        con.commit()
    }

    @Test
    fun `createDocument and getById returns a Document`() {
        trxManager.run {
            val documentCreated = repoDocument.createDocument("Doc1", "Newsletter", "filepath0")
            val documentGot = repoDocument.getById(documentCreated.id)
            val documentExpected = Document(id = 1, name = "Doc1", origin = "Newsletter", filePath = "filepath0")
            assertNotNull(documentGot)
            assertEquals(documentExpected, documentCreated)
            assertEquals(documentExpected, documentGot)
        }
    }

    @Test
    fun `createDocument and update its name, origin and filePath and check changes`() {
        trxManager.run {
            val documentCreated = repoDocument.createDocument("Doc1", "Newsletter", "filepath0")
            val documentGot = repoDocument.getById(documentCreated.id)
            assertEquals(documentCreated, documentGot)
            val updatedNameDocument = documentCreated.copy(name = "Document1")
            repoDocument.save(updatedNameDocument)
            assertNotEquals(updatedNameDocument.name, documentCreated.name)
            val updatedOriginDocument = documentCreated.copy(origin = "Repositório Científico")
            repoDocument.save(updatedOriginDocument)
            assertNotEquals(updatedOriginDocument.origin, documentCreated.origin)
            val updatedFilePathDocument = documentCreated.copy(filePath = "filePath0")
            assertNotEquals(updatedFilePathDocument.filePath, documentCreated.filePath)
            repoDocument.save(updatedFilePathDocument)
            val foundUpdated = repoDocument.getById(updatedFilePathDocument.id)
            assertEquals(updatedFilePathDocument, foundUpdated)
        }
    }

    @Test
    fun `getAll returns all Document`() {
        trxManager.run {
            val documentCreated = repoDocument.createDocument("Doc1", "Newsletter", "filepath0")
            val documentCreated1 = repoDocument.createDocument("Doc2", "Newsletter", "filepath1")
            val documentCreated2 = repoDocument.createDocument("Doc3", "Newsletter", "filepath2")
            val allDocument = repoDocument.getAll()
            assertEquals(3, allDocument.size)
            assertEquals(listOf(documentCreated, documentCreated1, documentCreated2), allDocument)
        }
    }

    @Test
    fun `getDocumentByName returns a list of Documents associated with a given Document Name`() {
        trxManager.run {
            val documentCreated = repoDocument.createDocument("Doc1", "Newsletter", "filepath0")
            val documentCreated1 = repoDocument.createDocument("Doc1", "RepoCientífico", "filepath1")
            val documentNotAppear = repoDocument.createDocument("Doc2", "Newsletter", "filepath0") //should not appear
            val foundDocuments = repoDocument.getDocumentsByName("Doc1")
            assertEquals(2, foundDocuments.size)
            assertFalse(foundDocuments.contains(documentNotAppear))
            assertEquals(listOf(documentCreated, documentCreated1), foundDocuments)
        }
    }

    @Test
    fun `getOrigin returns the origin of a given Document`() {
        trxManager.run {
            val documentCreated = repoDocument.createDocument("Doc1", "Newsletter", "filepath0")
            val foundOrigin = repoDocument.getOrigin(documentCreated.id)
            val expectedOrigin = "Newsletter"
            assertEquals(expectedOrigin, foundOrigin)
        }
    }

    @Test
    fun `getFilePath returns the file path of a given Document`() {
        trxManager.run {
            val documentCreated = repoDocument.createDocument("Doc1", "Newsletter", "filepath0")
            val foundFP = repoDocument.getFilepath(documentCreated.id)
            val expectedFP = "filepath0"
            assertEquals(expectedFP, foundFP)
        }
    }

    @Test
    fun `deleteById removes the Document`() {
        trxManager.run {
            val document = repoDocument.createDocument("Doc1", "Newsletter", "filepath0")
            val documentDeleted = repoDocument.deleteById(document.id)
            val shouldBeNull = repoDocument.getById(document.id)
            assertEquals(true, documentDeleted)
            assertNull(shouldBeNull)
        }
    }

    @Test
    fun `clear should clear all the repo`() {
        trxManager.run {
            val document = repoDocument.createDocument("Doc1", "Newsletter", "filepath0")
            val document1 = repoDocument.createDocument("Doc2", "Newsletter", "filepath1")
            val document2 = repoDocument.createDocument("Doc3", "Newsletter", "filepath2")
            repoDocument.clear()
            val getShouldBeNull = repoDocument.getById(document.id)
            val getShouldBeNull1 = repoDocument.getById(document1.id)
            val getShouldBeNull2 = repoDocument.getById(document2.id)
            val shouldBeEmpty = repoDocument.getAll()
            assertEquals(0, shouldBeEmpty.size)
            assertNull(getShouldBeNull)
            assertNull(getShouldBeNull1)
            assertNull(getShouldBeNull2)
        }
    }
}