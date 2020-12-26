                               SQLPi Test Server
This project is developed as SQLPi test server. It implements the following
simple behavior:
    1. Echo.
    2. Compare to a fixed random value with a given comparison operator.
    3. Simple blind injection test instance.
    4. Blind injection test instance with a simple WAF.
    5. Blind injection test instance with a high latency network.
    6. Get the fixed random value.
    7. Get or reset inject count.
    8. Get or reset compare count.
    9. Get or reset request count.
    10. Reset all count.
And their URL and expected params are:
    1. /echo?msg=
    2. /compare/<string:comp>?val=[?target=]
    3. /inject/simple?inject=
    4. /inject/waf?inject=
    5. /inject/latency?inject=
    6. /debug/target
    7. /debug/inject-count[?reset]
    8. /debug/compare-count[?reset]
    9. /debug/request-count[?reset]
    10. /debug/reset
Have fun!
