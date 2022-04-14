% Use this editor as a MiniZinc scratch book
include "globals.mzn"; 

% Row one Item Quantity Row Two Price
int:n;

%array[1..n] of int: selecteQuantites;

array[1..n] of int: ProduceQuantity;
array[1..n] of float: DistanceBetween;
array[1..n] of float: Prices;

int:quantity;

float: maxdistance;
float: maxprice;
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
%constraint forall(i in 1..n)((SelectedProduces[i] * DistanceBetween[i])<=(SelectedProduces[i]*Prices[i]));

var float: choosenlocation;
var float :byprice=sum(j in 1..n)(SelectedProduces[j]*Prices[j]);
var float :byDistance=sum(j in 1..n)(SelectedProduces[j]*DistanceBetween[j]);


%constraint
%choosenlocation =if byprice<=byDistance then byprice else byDistance endif;
choosenlocation=0.6*byprice+0.4*byDistance;


solve minimize choosenlocation;


