import tkinter as tk
from tkinter import ttk

class RecipeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Yemek Tarifleri")
        self.root.geometry("600x500")

        self.recipes = {
            "Mercimek Çorbası": {
                "malzemeler": [
                    "1 su bardağı kırmızı mercimek",
                    "1 adet soğan",
                    "1 adet havuç",
                    "1 yemek kaşığı domates salçası",
                    "6 su bardağı sıcak su",
                    "Tuz, karabiber, nane",
                    "Zeytinyağı"
                ],
                "yapilisi": [
                    "Mercimekleri yıkayıp süzün.",
                    "Soğanı ve havucu küp küp doğrayın.",
                    "Tencerede zeytinyağını ısıtıp soğan ve havuçları kavurun.",
                    "Salçayı ekleyip kokusu çıkana kadar kavurun.",
                    "Mercimekleri ve sıcak suyu ekleyin. Tuz ve karabiberi ayarlayın.",
                    "Mercimekler yumuşayana kadar pişirin.",
                    "Blenderdan geçirin veya tel süzgeçle ezin.",
                    "Üzerine nane ve zeytinyağı gezdirerek servis yapın."
                ]
            },
            "Tavuk Sote": {
                "malzemeler": [
                    "500 gr tavuk göğsü",
                    "2 adet sivri biber",
                    "1 adet kırmızı biber",
                    "1 adet soğan",
                    "2 diş sarımsak",
                    "1 yemek kaşığı domates salçası",
                    "Tuz, karabiber, kekik",
                    "Sıvı yağ"
                ],
                "yapilisi": [
                    "Tavuk göğsünü kuşbaşı doğrayın.",
                    "Soğanı ve biberleri iri iri doğrayın. Sarımsakları ince ince kıyın.",
                    "Geniş bir tavada sıvı yağı ısıtın ve tavukları suyunu salıp çekene kadar kavurun.",
                    "Soğanları ekleyip pembeleşinceye kadar kavurun.",
                    "Biberleri ve sarımsakları ekleyip birkaç dakika daha kavurun.",
                    "Salçayı ekleyip karıştırın.",
                    "Tuz, karabiber ve kekiği ekleyin.",
                    "Kısık ateşte sebzeler yumuşayana kadar pişirin."
                ]
            },
            "Pirinç Pilavı": {
                "malzemeler": [
                    "2 su bardağı pirinç",
                    "3 su bardağı sıcak su",
                    "2 yemek kaşığı tereyağı",
                    "1 yemek kaşığı sıvı yağ",
                    "Tuz"
                ],
                "yapilisi": [
                    "Pirinci tuzlu sıcak suda 20 dakika bekletin, sonra yıkayıp süzün.",
                    "Tencerede tereyağı ve sıvı yağı eritin.",
                    "Pirinci ekleyip şeffaflaşana kadar kavurun.",
                    "Sıcak suyu ve tuzu ekleyin.",
                    "Kaynamaya başlayınca altını kısıp suyunu çekene kadar pişirin.",
                    "Ocaktan alıp 10-15 dakika demlendirin."
                ]
            }
        }

        self.create_widgets()

    def create_widgets(self):
        # Tarif listesi için Frame
        list_frame = ttk.Frame(self.root, padding="10")
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Tarif listesi başlığı
        ttk.Label(list_frame, text="Tarifler", font=("Arial", 16, "bold")).pack(pady=10)

        # Tarifleri listelemek için Listbox
        self.recipe_listbox = tk.Listbox(list_frame, font=("Arial", 12), height=15)
        for recipe_name in self.recipes.keys():
            self.recipe_listbox.insert(tk.END, recipe_name)
        self.recipe_listbox.pack(fill=tk.BOTH, expand=True)
        self.recipe_listbox.bind("<<ListboxSelect>>", self.show_recipe)

        # Tarif detayları için Frame
        detail_frame = ttk.Frame(self.root, padding="10")
        detail_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Tarif detayları başlığı
        self.detail_title = ttk.Label(detail_frame, text="Bir tarif seçin", font=("Arial", 16, "bold"))
        self.detail_title.pack(pady=10)

        # Malzemeler başlığı
        ttk.Label(detail_frame, text="Malzemeler:", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        self.ingredients_label = ttk.Label(detail_frame, text="", font=("Arial", 10), wraplength=300, justify=tk.LEFT)
        self.ingredients_label.pack(fill=tk.X, pady=5)

        # Yapılışı başlığı
        ttk.Label(detail_frame, text="Yapılışı:", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        self.instructions_label = ttk.Label(detail_frame, text="", font=("Arial", 10), wraplength=300, justify=tk.LEFT)
        self.instructions_label.pack(fill=tk.X, pady=5)

    def show_recipe(self, event):
        selected_indices = self.recipe_listbox.curselection()
        if selected_indices:
            selected_recipe_name = self.recipe_listbox.get(selected_indices[0])
            recipe_data = self.recipes[selected_recipe_name]

            self.detail_title.config(text=selected_recipe_name)

            ingredients_text = "\n".join(recipe_data["malzemeler"])
            self.ingredients_label.config(text=ingredients_text)

            instructions_text = "\n".join(recipe_data["yapilisi"])
            self.instructions_label.config(text=instructions_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = RecipeApp(root)
    root.mainloop()
