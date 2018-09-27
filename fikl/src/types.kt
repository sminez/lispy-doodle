package fikl

/**
 * Placeholder type to allow for dynamic typing in the interpretor
 */
typealias LispVal = Any

typealias LispFunc = (vals: LispVector) -> LispVal

// Internal types
typealias Symbol = String
typealias KeyWord = String
typealias LispVector = Array<LispVal>
typealias LispList = List<LispVal>
typealias LispMap = HashMap<LispVal, LispVal>
typealias LispSet = HashSet<LispVal>
typealias LispPair = Pair<LispVal, LispVal>


/**
 * A user defined procedure
 */
class Procedure(params: LispVector, body: LispVector, env: Environment, evaluator: Evaluator) {
    val params = params
    val body = body
    val env = env
    val evaluator = evaluator

    init {

    }
}
