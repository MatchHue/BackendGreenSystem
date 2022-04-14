% Use this editor as a MiniZinc scratch book
include "globals.mzn"; 

% Row one Item Quantity Row Two Price
int:n;

%array[1..n] of int: selecteQuantites;

array[1..n] of int: ProduceQuantity;
array[1..n] of float: DistanceBetween;

int:quantity;

var int:sumItems;
var int:totalProducts;


totalProducts = sum(i in 1..n)( ProduceQuantity[i]);

constraint totalProducts>=quantity;

array[1..n] of var int: SelectedProduces;

constraint forall(i in 1..n)(SelectedProduces[i] >= 0);

%constraint alldifferent(SelectedProduces);

sumItems = sum(i in 1..n)(SelectedProduces[i]);
constraint sumItems >= quantity;
constraint sumItems <= totalProducts;

constraint forall(i in 1..n)( SelectedProduces[i] <= ProduceQuantity[i]);

var float: choosenlocation;
choosenlocation = sum(j in 1..n)(if SelectedProduces[j]>0 then DistanceBetween[j] else 0 endif);

solve minimize choosenlocation;


