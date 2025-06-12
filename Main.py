import xml.etree.ElementTree as ET
import pandas as pd
import re
from pathlib import Path


# OSM
def parse_opening_hours(hours_str):
    try:
        match = re.search(r'(\d{2}):(\d{2})', hours_str)
        if match:
            hour = int(match.group(1))
            return f'{hour:02d}:00'
        return 'Неизвестное время открытия'
    except Exception:
        return 'Неизвестное время открытия'


def get_restaurants_from_osm_file(osm_file):
    try:
        tree = ET.parse(osm_file)
        root = tree.getroot()
    except Exception as e:
        raise ValueError(f'Ошибка при чтении файла {osm_file}: {e}')

    restaurants = []
    for node in root.findall(".//node") + root.findall(".//way"):
        is_restaurant = False
        name = 'Без названия'
        phone = 'Телефон неизвестен'
        website = 'Сайт неизвестен'
        opening_hours = 'Неизвестное время открытия'

        for tag in node.findall('tag'):
            key = tag.get('k')
            value = tag.get('v')
            if key == 'amenity' and value == 'restaurant':
                is_restaurant = True
            if key == 'name':
                name = value
            if key == 'phone':
                phone = value
            if key == 'website':
                website = value

        if is_restaurant:
            opening_hour = parse_opening_hours(opening_hours)
            restaurants.append({
                'name': name,
                'phone': phone,
                'website': website,
                'opening_hour': opening_hour
            })

    df = pd.DataFrame(restaurants)
    grouped = df.groupby('opening_hour').apply(
        lambda x: x[['name', 'phone', 'website']].to_dict('records')
    ).to_dict()

    return grouped


def print_restaurants(grouped_restaurants):
    for opening_hour in sorted(grouped_restaurants.keys()):
        print(f'\nРестораны, открывающиеся в {opening_hour}:')
        restaurants = grouped_restaurants[opening_hour]
        if not restaurants:
            print('  Нет ресторанов.')
            continue
        for restaurant in restaurants:
            print(f"  - {restaurant['name']}, Телефон: {restaurant['phone']}, Сайт: {restaurant['website']}")


# Main
def main():
    # '12.osm'    '12 -2.osm'
    osm_file = Path('__file__').resolve().parent / 'OsmData' / '12.osm'
    try:
        grouped_restaurants = get_restaurants_from_osm_file(osm_file)
        print_restaurants(grouped_restaurants)
    except Exception as e:
        print(f'Ошибка при обработке данных: {e}')


if __name__ == '__main__':
    main()