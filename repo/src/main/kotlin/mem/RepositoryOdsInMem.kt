package mem

import Ods
import RepositoryOds
import Terms

class RepositoryOdsInMem: RepositoryOds {
    private val ods = mutableListOf<Ods>(
        Ods(0, "Erradicação da Pobreza"),
        Ods(1, "Fome Zero"),
        Ods(2, "Boa Saúde e Bem-Estar"),
        Ods(3, "Educação de Qualidade"),
        Ods(4, "Igualdade de Género"),
        Ods(5, "Água Limpa e Saneamento"),
        Ods(6, "Energia Acessível e Limpa"),
        Ods(7, "Emprego Digno e Crescimento Económico"),
        Ods(8, "Indústria, Inovação e Infraestrutura"),
        Ods(9, "Redução das Desigualdades"),
        Ods(10, "Cidades e Comunidades Sustentáveis"),
        Ods(11, "Consumo e Produção Responsáveis"),
        Ods(12, "Combate às Alterações Climáticas"),
        Ods(13, "Vida de Baixo D'Água"),
        Ods(14, "Vida Sobre a Terra"),
        Ods(15, "Paz, Justiça e Instituições Fortes"),
        Ods(16, "Parcerias Emprol das Metas"),
    )
    override fun getById(id: Int): Ods? = ods.find { it.id == id }

    override fun findByName(name: String): Ods? = ods.find { it.name == name }

    override fun getAll(): List<Ods> = ods.toList()

    override fun save(entity: Ods) {
        ods.removeIf { it.id == entity.id }
        ods.add(entity)
    }

    override fun deleteById(id: Int): Boolean = ods.removeIf { it.id == id }

    override fun clear() = ods.clear()
}