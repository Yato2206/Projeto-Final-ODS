package pt.isel.ps

interface RepositoryTerms: Repository<Terms> {
     fun findByName(name: String): Terms?
     fun getAllOdsTerms(odsId: Int): List<Terms>
     fun createTerm(odsId: Int, name: String, origin: String): Terms
}