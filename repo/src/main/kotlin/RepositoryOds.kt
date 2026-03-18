interface RepositoryOds: Repository<Ods> {
    fun findByName(name: String): Ods?
    fun getAllAvailable(): List<Ods>
    fun getAllTerms(ods: Ods): List<Terms>
}