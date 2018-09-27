package fikl

/**
 * An Environment is a map of known Symbols to values that we can
 * resolve bindings in, along with a reference to the enclosing
 * environment (scope) that we can backtrack to.
 *
 * @constructor Create a new environment with an optional outer scope.
 */
open class Environment(outer: Environment?) {
    private val bindings = LispMap()
    private val outer = outer

    /**
     * Attempt to find the closest environment to the lookup site
     * that contains a binding for `sym`.
     *
     * @param[sym] The symbol being looked up
     * @return The environment containing the binding or null
     */
    fun find(sym: Symbol): Environment? {
       if (bindings.containsKey(sym)) {
           return this
       }
       return outer?.find(sym)
    }
}


/**
 * The global environment containing builtin functions and declarations
 */
object GlobalEnvironment: Environment(null) {
    val bindings = hashMapOf(
            Pair("+", {a: LispList -> a.reduce({x, y -> x as Double + y as Double})}),
            Pair("-", {a: LispList -> a.reduce({x, y -> x as Double - y as Double})}),
            Pair("*", {a: LispList -> a.reduce({x, y -> x as Double * y as Double})}),
            Pair("/", {a: LispList -> a.reduce({x, y -> x as Double / y as Double})}),
            Pair("%", {a: LispList -> a[0] as Int % a[1] as Int}),
            Pair("<", {a: LispList -> a.reduce({x, y -> x < y})}),
            //Pair(">", ),
            //Pair("<=", ),
            //Pair(">=", ),
            //Pair("==", ),
            //Pair("eq?", ),
            //Pair("null?", {a: LispList -> a[0] == null}),
            Pair("int?", {a: LispList -> a[0] is Int}),
            Pair("float?", {a: LispList -> a[0] is Float}),
            Pair("double?", {a: LispList -> a[0] is Double}),
            Pair("string?", {a: LispList -> a[0] is String}),
            Pair("symbol?", {a: LispList -> a[0] is Symbol}),
            Pair("keyword?", {a: LispList -> a[0] is KeyWord}),
            Pair("list?", {a: LispList -> a[0] is List<*>}),
            Pair("pair?", {a: LispList -> a[0] is Pair<*, *>}),
            Pair("car", {a: LispList -> a[0]}),
            Pair("cdr", {a: LispList -> a.subList(1, a.size)}),
            Pair("head", {a: LispList -> a[0]}),
            Pair("tail", {a: LispList -> a.subList(1, a.size)}),
            Pair("cons", {a: LispList ->
                val newList = mutableListOf(a[0])
                newList.addAll(a.subList(1, a.size))
                newList
            }),
            Pair("len", {a: LispList -> a.size}),
            //Pair("append", append),
            //Pair("range", range),
    )
}