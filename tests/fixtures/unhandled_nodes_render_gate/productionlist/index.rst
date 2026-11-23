Grammar
=======

.. productionlist::
   expr: `term` ("+" `term`)*
   term: `factor` ("*" `factor`)*
   factor: NUMBER
         : | "(" `expr` ")"
         : | "-" `factor`

.. productionlist:: grp
   stmt: `expr` ";"

The :token:`expr` rule and the grouped :token:`grp:stmt` rule are linked.
An unresolved :token:`nosuchtoken` stays plain text.
