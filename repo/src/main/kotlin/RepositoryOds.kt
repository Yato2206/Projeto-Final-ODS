interface RepositoryOds: Repository<Ods> {
    fun findByName(name: String): Ods?
}