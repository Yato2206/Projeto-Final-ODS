package pt.isel.ps

import jdbc.pt.isel.ps.DatabaseConnection
import jdbc.pt.isel.ps.TransactionManagerJdbc
import org.junit.jupiter.api.Test
import kotlin.test.*

class RepositoryJdbcTermsTest {
    companion object {
        val trxManager = TransactionManagerJdbc()
        val con = DatabaseConnection.getConnection()
    }

    @BeforeTest
    fun setup() {
        val sql = "TRUNCATE dbo.terms, dbo.ods RESTART IDENTITY CASCADE;"
        con.prepareStatement(sql).use { stmt ->
            stmt.executeUpdate()
        }
        con.commit()
    }

    @Test
    fun `createTerm and getById returns a Term`() {
        trxManager.run {
            val ods = repoOds.createOds("Erradicação da Pobreza")
            val termCreated = repoTerms.createTerm(ods.id, "poverty", "Origin1")
            val termGot = repoTerms.getById(termCreated.id)
            val termExpected = Terms(1, 1, "poverty", "Origin1")
            assertNotNull(termGot)
            assertEquals(termExpected, termCreated)
            assertEquals(termExpected, termGot)
        }
    }

    @Test
    fun `findByName returns a Term`() {
        trxManager.run {
            val ods = repoOds.createOds("Erradicação da Pobreza")
            val termCreated = repoTerms.createTerm(ods.id, "poverty", "Origin1")
            val termGot = repoTerms.findByName("poverty")
            assertNotNull(termGot)
            assertEquals(termCreated, termGot)
        }
    }


    @Test
    fun `createTerm and update its ods, name and origin and check changes`() {
        trxManager.run {
            val ods = repoOds.createOds("Erradicação da Pobreza")
            val ods1 = repoOds.createOds("Fome Zero")
            val termCreated = repoTerms.createTerm(ods.id, "poverty", "Origin1")
            val termGot = repoTerms.getById(termCreated.id)
            assertEquals(termCreated, termGot)
            val updatedOdsIdTerm = termCreated.copy(odsId = ods1.id)
            repoTerms.save(updatedOdsIdTerm)
            assertNotEquals(updatedOdsIdTerm.odsId, termCreated.odsId)
            val updatedNameTerm = termCreated.copy(name = "Test Term")
            repoTerms.save(updatedNameTerm)
            assertNotEquals(updatedNameTerm.name, termCreated.name)
            val updatedOriginTerm = termCreated.copy(origin = "Test Origin")
            repoTerms.save(updatedOriginTerm)
            assertNotEquals(updatedOriginTerm.origin, termCreated.origin)
            val foundUpdated = repoTerms.getById(termCreated.id)
            assertEquals(updatedOriginTerm, foundUpdated)
        }
    }

    @Test
    fun `getAll returns all Terms`() {
        trxManager.run {
            val ods = repoOds.createOds("Erradicação da Pobreza")
            val ods1 = repoOds.createOds("Fome Zero")
            val ods2 = repoOds.createOds("Boa Saúde e Bem-Estar")
            val term = repoTerms.createTerm(ods.id, "poverty", "Origin1")
            val term1 = repoTerms.createTerm(ods1.id,"homeless", "Origin1")
            val term2 = repoTerms.createTerm(ods2.id,"precarity", "Origin2")
            val allTerms = repoTerms.getAll()
            assertEquals(3, allTerms.size)
            assertEquals(listOf(term, term1, term2), allTerms)
        }
    }

    @Test
    fun `getAllOdsTerms returns all Terms associated with a given ODS`() {
        trxManager.run {
            val ods = repoOds.createOds("Erradicação da Pobreza")
            val ods1 = repoOds.createOds("Fome Zero")
            val term = repoTerms.createTerm(ods.id, "poverty", "Origin1")
            val term1 = repoTerms.createTerm(ods.id,"homeless", "Origin1")
            repoTerms.createTerm(ods1.id,"precarity", "Origin2")
            val allUsers = repoTerms.getAllOdsTerms(ods.id)
            assertEquals(2, allUsers.size)
            assertEquals(listOf(term, term1), allUsers)
        }
    }

    @Test
    fun `deleteById removes the Term`() {
        trxManager.run {
            val ods = repoOds.createOds("Erradicação da Pobreza")
            val term = repoTerms.createTerm(ods.id, "poverty", "Origin1")
            val termDeleted = repoTerms.deleteById(term.id)
            val shouldBeNull = repoTerms.getById(term.id)
            assertEquals(true, termDeleted)
            assertNull(shouldBeNull)
        }
    }

    @Test
    fun `clear should clear all the repo`() {
        trxManager.run {
            val ods = repoOds.createOds("Erradicação da Pobreza")
            val ods1 = repoOds.createOds("Fome Zero")
            val ods2 = repoOds.createOds("Boa Saúde e Bem-Estar")
            val term = repoTerms.createTerm(ods.id, "poverty", "Origin1")
            val term1 = repoTerms.createTerm(ods1.id,"homeless", "Origin1")
            val term2 = repoTerms.createTerm(ods2.id,"precarity", "Origin2")
            repoTerms.clear()
            val getShouldBeNull = repoTerms.getById(term.id)
            val getShouldBeNull1 = repoTerms.getById(term1.id)
            val getShouldBeNull2 = repoTerms.getById(term2.id)
            val shouldBeEmpty = repoTerms.getAll()
            assertEquals(0, shouldBeEmpty.size)
            assertNull(getShouldBeNull)
            assertNull(getShouldBeNull1)
            assertNull(getShouldBeNull2)
        }
    }
}