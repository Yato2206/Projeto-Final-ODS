interface RepositoryTerms: Repository<Terms> {
     fun findByName(name: String): Terms?
}