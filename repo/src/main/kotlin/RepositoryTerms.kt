interface RepositoryTerms: Repository<Terms> {
     fun findByName(name: String): Terms?
     fun getAllTerms(ods: Ods): List<Terms>
}