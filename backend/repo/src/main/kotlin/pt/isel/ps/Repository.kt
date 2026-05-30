package pt.isel.ps

interface Repository<T> {
    fun getById(id: Int): T? // Get an entity by its ID

    fun getAll(): List<T> // Retrieve all entities

    fun save(entity: T) // Save a new or existing entity

    fun deleteById(id: Int): Boolean // Delete an entity by its ID

    fun clear() // Delete all entries
}