from recipes.models import IngredientRecipeAmount, ShoppingCart


def generate_shopping_list(user):
    ing_list = {}
    text = 'Ваш список покупок: \n\n'
    recipes_in_shopping_cart = ShoppingCart.objects.filter(user=user)
    for recipe in recipes_in_shopping_cart:
        ingredient_recipe = IngredientRecipeAmount.objects.filter(
            recipe=recipe.recipe)
        for element in ingredient_recipe:
            if element.ingredient.name in ing_list:
                ing_list[element.ingredient.name]['Количество'] += (
                    element.amount)
            else:
                ing_list.update(
                    {element.ingredient.name: {
                        'Количество': element.amount,
                        'Единицы': element.ingredient.measurement_unit}})
    for ing in ing_list:
        amount = ing_list[ing]['Количество']
        unit = ing_list[ing]['Единицы']
        text += ing + ' ' + str(amount) + ' ' + unit + '\n'
    return text
