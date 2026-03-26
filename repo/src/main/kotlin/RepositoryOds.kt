interface RepositoryOds: Repository<Ods> {
    fun findByName(name: String): Ods?
    fun createOds(name:String): Ods
}