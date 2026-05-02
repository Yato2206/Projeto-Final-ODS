package pt.isel.ps

import jdbc.pt.isel.ps.DatabaseConnection
import jdbc.pt.isel.ps.TransactionManagerJdbc
import org.junit.jupiter.api.Test
import java.time.LocalDateTime
import kotlin.test.*

class RepositoryJdbcDataTest {
    companion object {
        val trxManager = TransactionManagerJdbc()
        val con = DatabaseConnection.getConnection()
    }
    private val fixedDate = LocalDateTime.of(2026, 3, 25, 0, 0)

    @BeforeTest
    fun setup() {
        val sql = "TRUNCATE dbo.data, dbo.ods RESTART IDENTITY CASCADE;"
        con.prepareStatement(sql).use { stmt ->
            stmt.executeUpdate()
        }
        con.commit()
    }

    @Test
    fun `createData and getById returns a Data`() {
        trxManager.run {
            val dataCreated = repoData.createData("Origin1", fixedDate)
            val dataGot = repoData.getById(dataCreated.id)
            val dataExpected = Data(id = 1, origin = "Origin1", dateChecked = fixedDate)
            assertNotNull(dataGot)
            assertEquals(dataExpected, dataCreated)
            assertEquals(dataExpected, dataGot)
        }
    }

    @Test
    fun `createData and update its ods, type and dateChecked and check changes`() {
        trxManager.run {
            val dataCreated = repoData.createData("Origin1", fixedDate)
            val dataGot = repoData.getById(dataCreated.id)
            assertEquals(dataCreated, dataGot)
            val ods = repoOds.createOds("Erradicação da Pobreza")
            val updatedOdsIdData = dataCreated.copy(odsId = listOf(ods.id))
            repoData.save(updatedOdsIdData)
            assertNotEquals(updatedOdsIdData.odsId, dataCreated.odsId)
            val updatedTypeData = dataCreated.copy(type = DataType.CIENTIFICO)
            repoData.save(updatedTypeData)
            assertNotEquals(updatedTypeData.type, dataCreated.type)
            val updatedDateCheckedData = dataCreated.copy(dateChecked = fixedDate.plusDays(1))
            repoData.save(updatedDateCheckedData)
            assertNotEquals(updatedDateCheckedData.dateChecked, dataCreated.dateChecked)
            val foundUpdated = repoData.getById(updatedDateCheckedData.id)
            assertEquals(updatedDateCheckedData, foundUpdated)
        }
    }

    @Test
    fun `getAll returns all Data`() {
        trxManager.run {
            val dataCreated = repoData.createData("Origin1", fixedDate)
            val dataCreated1 = repoData.createData("Origin2", fixedDate)
            val dataCreated2 = repoData.createData("Origin3", fixedDate)
            val allData = repoData.getAll()
            assertEquals(3, allData.size)
            assertEquals(listOf(dataCreated,dataCreated1, dataCreated2), allData)
        }
    }

    @Test
    fun `getOds returns a list of ODS associated with a given Data`() {
        trxManager.run {
            val dataCreated = repoData.createData("Origin1", fixedDate)
            val ods = repoOds.createOds("Erradicação da Pobreza")
            val ods1 = repoOds.createOds("Fome Zero")
            val ods2 = repoOds.createOds("Boa Saúde e Bem-Estar")
            val dataWithOds = dataCreated.copy(odsId = listOf(ods.id, ods1.id, ods2.id))
            repoData.save(dataWithOds)
            val foundOds = repoData.getOds(dataWithOds.id)
            assertEquals(3, foundOds.size)
            assertEquals(listOf(ods,ods1,ods2), foundOds)
        }
    }

    @Test
    fun `getOrigin returns the origin of a given Data`() {
        trxManager.run {
            val dataCreated = repoData.createData("Origin1", fixedDate)
            val foundOds = repoData.getOrigin(dataCreated.id)
            val expectedOrigin = "Origin1"
            assertEquals(expectedOrigin, foundOds)
        }
    }

    @Test
    fun `getType returns the type of a given Data`() {
        trxManager.run {
            val dataCreated = repoData.createData("Origin1", fixedDate)
            val foundOds = repoData.getType(dataCreated.id)
            val expectedType = DataType.UNDEFINED
            assertEquals(expectedType, foundOds)
        }
    }

    @Test
    fun `getDateChecked returns the checked date of a given Data`() {
        trxManager.run {
            val dataCreated = repoData.createData("Origin1", fixedDate)
            val foundOds = repoData.getDateChecked(dataCreated.id)
            val expectedDate = fixedDate
            assertEquals(expectedDate, foundOds)
        }
    }

    @Test
    fun `deleteById removes the Data`() {
        trxManager.run {
            val data = repoData.createData("Origin1", fixedDate)
            val dataDeleted = repoData.deleteById(data.id)
            val shouldBeNull = repoData.getById(data.id)
            assertEquals(true, dataDeleted)
            assertNull(shouldBeNull)
        }
    }

    @Test
    fun `clear should clear all the repo`() {
        trxManager.run {
            val data = repoData.createData("Origin1", fixedDate)
            val data1 = repoData.createData("Origin2", fixedDate)
            val data2 = repoData.createData("Origin3", fixedDate)
            repoData.clear()
            val getShouldBeNull = repoData.getById(data.id)
            val getShouldBeNull1 = repoData.getById(data1.id)
            val getShouldBeNull2 = repoData.getById(data2.id)
            val shouldBeEmpty = repoData.getAll()
            assertEquals(0, shouldBeEmpty.size)
            assertNull(getShouldBeNull)
            assertNull(getShouldBeNull1)
            assertNull(getShouldBeNull2)
        }
    }
}