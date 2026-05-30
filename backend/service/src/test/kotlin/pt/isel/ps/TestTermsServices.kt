package pt.isel.ps

import org.example.Failure
import org.example.Success
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.test.annotation.DirtiesContext
import org.springframework.test.context.junit.jupiter.SpringJUnitConfig
import kotlin.test.assertEquals
import kotlin.test.assertIs

@SpringJUnitConfig(TestConfig::class)
@DirtiesContext(classMode = DirtiesContext.ClassMode.AFTER_EACH_TEST_METHOD)
class TestTermsServices {

    @Autowired
    private lateinit var service: TermsServices

    @Test
    fun `createTerm creates a new term`() {
        val term = service.createTerm(
            name = "pedagogy",
            odsId = 4,
            origin = "Universidade de Toronto"
        )
        assertIs<Success<Terms>>(term)
        assertEquals(9, term.value.id)
        assertEquals("pedagogy", term.value.name)
        assertEquals(4, term.value.odsId)
        assertEquals("Universidade de Toronto", term.value.origin)
    }

    @Test
    fun `createTerm returns error because Term already exists`() {
        val term = service.createTerm(
            name = "poverty",
            odsId = 4,
            origin = "Universidade de Toronto"
        )
        assertIs<Failure<TermsError.TermAlreadyExists>>(term)
    }

    @Test
    fun `getAllOdsTerms returns a list of terms`() {
        val terms = service.getAllOdsTerms(
            odsId = 2,
        )
        val expected = listOf<Terms>(
            Terms(6, 2, "well being", "Universidade de Toronto"),
            Terms(7, 2, "holism", "Universidade de Toronto"),
            Terms(8, 2, "epidemics", "Universidade de Toronto"))
        assertIs<Success<List<Terms>>>(terms)
        val termsList = terms.value
        assertEquals(expected, termsList)
    }

    @Test
    fun `getAllOdsTerms from an ods that doesnt exist`() {
        val terms = service.getAllOdsTerms(odsId = 23)
        assertIs<Failure<TermsError.OdsNotFound>>(terms)
    }

    @Test
    fun `deleteTerms deletes a term`() {
        val deleted = service.deleteTerms(7)
        assertIs<Success<Boolean>>(deleted)
        val deletedValue = deleted.value
        assertEquals(true, deletedValue)
    }

    @Test
    fun `deleteTerms fails to delete a term`() {
        val deleted = service.deleteTerms(23)
        assertIs<Failure<TermsError.NotFound>>(deleted)
    }
}