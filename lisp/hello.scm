; To be used for testing Scheme later on

(define first car)
(define rest cdr)

(define count 
    (lambda (item L) 
        (if L ; since L can be empty list, works as test condition
            (+ (equal? item (first L)) (count item (rest L)))
            0)))

; (define fact (lambda (n) (if (<= n 1) 1 (* n (fact (- n 1))))))
(define fact 
    (lambda (n) 
        (if (<= n 1) 
            1 
            (* n (fact (- n 1))))))

(define fib 
    (lambda (n) 
        (if (< n 2) 
            1 
            (+ (fib (- n 1)) (fib (- n 2))))))

; (define range (lambda (a b) (if (= a b) (quote ()) (cons a (range (+ a 1) b)))))
; (define range (lambda (a b) (if (= a b) ('()) (cons a (range (+ a 1) b)))))
(define range 
    (lambda (a b) 
        (if (= a b) 
            ('()) 
            (cons a (range (+ a 1) b)))))

(map (lambda (x) (* x 2)) (quote (1 2 3 4 5 6)))

