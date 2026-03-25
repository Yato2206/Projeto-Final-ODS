import mem.RepositoryDataInMem
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.assertNotNull
import java.time.LocalDateTime
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNull

class RepositoryMemDataTest {
    private lateinit var repo: RepositoryDataInMem

    private val fixedDate = LocalDateTime.of(2026, 3, 25, 0, 0)

    @BeforeEach
    fun setUp() {
        repo = RepositoryDataInMem()
    }

    @Test
    fun `get a Data by ID`() {
        val found = repo.getById(0)
        assertEquals(Data(id = 0, odsId = listOf(1), type = DataType.ARTISTICO, origin = "Origin1", dateChecked = fixedDate), found)
    }

    @Test
    fun `get an inexistent Data by ID`() {
        val found = repo.getById(10)
        assertNull(found)
    }

    @Test
    fun `getAll Data entries`() {
        val found = repo.getAll()
        val dataList = listOf<Data>(
            Data(id = 0, odsId = listOf(1), type = DataType.ARTISTICO, origin = "Origin1", dateChecked = fixedDate),
            Data(id = 1, odsId = listOf(3, 17), type = DataType.CIENTIFICO, origin = "Origin2", dateChecked = fixedDate),
            Data(id = 2, odsId = listOf(5, 6, 7), type = DataType.ACAO_NA_SOCIEDADE, origin = "Origin1", dateChecked = fixedDate),
            Data(id = 3, odsId = listOf(), type = DataType.ARTISTICO, origin = "Origin4", dateChecked = fixedDate),
            Data(id = 4, odsId = listOf(4, 8, 11), type = DataType.ENSINO, origin = "Origin5", dateChecked = fixedDate),)
        assertEquals(dataList.size, found.size)
        assertEquals(dataList, found)
    }

    @Test
    fun `save updates an existent Data`() {
        val newDateChecked = LocalDateTime.of(2026, 3, 25, 6, 7)
        val updatedData = Data(0, listOf(1), DataType.CIENTIFICO, "Origin6", newDateChecked)
        repo.save(updatedData)
        val found = repo.getById(0)
        assertEquals(updatedData, found)
    }

    @Test
    fun `getOds returns the list of ODS associated with the Data`() {
        val foundData = repo.getById(0)
        assertNotNull(foundData)
        val foundOds = repo.getOds(foundData)
        assertEquals(listOf(Ods(1, "Fome Zero")), foundOds)
    }

    @Test
    fun `getOds returns an empty list due to no ODS associated with the Data`() {
        val foundData = repo.getById(3)
        assertNotNull(foundData)
        val foundOds = repo.getOds(foundData)
        assertEquals(0, foundOds.size)
        assertEquals(emptyList<Ods>(), foundOds)
    }

    @Test
    fun `getOrigin returns the origin of a Data`() {
        val found = repo.getOrigin(0)
        assertEquals("Origin1", found)
    }

    @Test
    fun `getType returns the dataType of a Data`() {
        val found = repo.getType(0)
        assertEquals(DataType.ARTISTICO, found)
    }

    @Test
    fun `getDateChecked returns the date checked of a Data`() {
        val found = repo.getDateChecked(0)
        assertEquals(fixedDate, found)
    }

    @Test
    fun `deleteById removes an existent Data`() {
        val found = repo.getById(0)
        assertEquals(Data(id = 0, odsId = listOf(1), type = DataType.ARTISTICO, origin = "Origin1", dateChecked = fixedDate), found)
        val deleted = repo.deleteById(0)
        assertEquals(true, deleted)
        val shouldBeNull = repo.getById(0)
        assertNull(shouldBeNull)
    }

    @Test
    fun `deleteById returns null`() {
        val deleted = repo.deleteById(10)
        assertEquals(false, deleted)
    }

    @Test
    fun `clear puts the Data list empty`() {
        val cleared = repo.clear()
        assertEquals(Unit, cleared)
        val foundData = repo.getById(0)
        assertNull(foundData)
        val foundList = repo.getAll()
        assertEquals(emptyList<Data>(), foundList)
        assertEquals(0, foundList.size)
    }
}