package pt.isel.ps

interface RepositoryOds: Repository<Ods> {
    fun findByName(name: String): Ods?
    fun createOds(name: String): Ods
}