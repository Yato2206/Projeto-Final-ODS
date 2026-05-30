package pt.isel.ps

import org.junit.jupiter.api.BeforeEach
import pt.isel.ps.mem.RepositoryTermsInMem
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNull

class RepositoryMemTermsTest {
    private lateinit var repo: RepositoryTerms

    @BeforeEach
    fun setUp() {
        repo = RepositoryTermsInMem()
    }

    @Test
    fun `create a Term` () {
        val create = repo.createTerm(0, "test term", "Universidade de Toronto")
        assertEquals(Terms(9, 0, "test term", "Universidade de Toronto"), create)
    }

    @Test
    fun `get Term by ID` () {
        val found = repo.getById(1)
        assertEquals(Terms(1, 0, "homeless", "Universidade de Toronto"), found)
    }

    @Test
    fun `get an inexistent Term by ID`() {
        val found = repo.getById(23)
        assertNull(found)
    }

    @Test
    fun `findByName returns correct Term`() {
        val found = repo.findByName("well being")
        assertEquals(Terms(6, 2, "well being", "Universidade de Toronto"), found)
    }

    @Test
    fun `findByName returns inexistent Terms (null)`() {
        val found = repo.findByName("Inexistent Term")
        assertNull(found)
    }

    @Test
    fun `getAll Terms`() {
        val found = repo.getAll()
        val termsList = listOf<Terms>(
            Terms(0, 0, "poverty", "Universidade de Toronto"),
            Terms(1, 0, "homeless", "Universidade de Toronto"),
            Terms(2, 0, "precarity", "Universidade de Toronto"),
            Terms(3, 1, "agriculture", "Universidade de Toronto"),
            Terms(4, 1, "nutrition", "Universidade de Toronto"),
            Terms(5, 1, "malnutrition", "Universidade de Toronto"),
            Terms(6, 2, "well being", "Universidade de Toronto"),
            Terms(7, 2, "holism", "Universidade de Toronto"),
            Terms(8, 2, "epidemics", "Universidade de Toronto")
        )
        assertEquals(termsList.size, found.size)
        assertEquals(termsList, found)
    }

    @Test
    fun `getAllOdsTerms of a given ODS`() {
        val ods = Ods(1, "Fome Zero")
        val found = repo.getAllOdsTerms(ods.id)
        val termsList = listOf<Terms>(
            Terms(3, 1, "agriculture", "Universidade de Toronto"),
            Terms(4, 1, "nutrition", "Universidade de Toronto"),
            Terms(5, 1, "malnutrition", "Universidade de Toronto")
        )
        assertEquals(termsList.size, found.size)
        assertEquals(termsList, found)
    }

    @Test
    fun `save updates an existing ODS`() {
        val updatedTerm = Terms(7, 2, "pollution", "Universidade de Toronto")
        repo.save(updatedTerm)
        val found = repo.getById(7)
        assertEquals(updatedTerm, found)
    }

    @Test
    fun `deleteById removes an existing Term`() {
        val found = repo.getById(2)
        assertEquals(Terms(2, 0, "precarity", "Universidade de Toronto"), found)
        val deleted = repo.deleteById(2)
        assertEquals(true, deleted)
        val shouldBeNull = repo.getById(2)
        assertNull(shouldBeNull)
    }

    @Test
    fun `deleteById returns null`() {
        val deleted = repo.deleteById(23)
        assertEquals(false, deleted)
    }

    @Test
    fun `clear puts the Terms list empty`() {
        val cleared = repo.clear()
        assertEquals(Unit, cleared)
        val foundTerm = repo.getById(0)
        assertNull(foundTerm)
        val foundList = repo.getAll()
        assertEquals(emptyList<Terms>(), foundList)
        assertEquals(0, foundList.size)
    }

}