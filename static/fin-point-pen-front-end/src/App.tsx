import { TasksList } from "./components/ListTasks/ListTask.tsx";
import { NavigationBar } from "./components/NavigationBar/NavigationBar.tsx";
import { Tasks } from "./components/Tasks/Tasks.tsx";
import { InputTasks } from "./components/Input/InputTasks.tsx";
import { InputBox } from "./components/InputBox/InputBox.tsx";
import { GroupTasks } from "./components/Input/GroupTasks.tsx/GroupTasks.tsx";
function App() {
  return (
    <>
      <main className=" h-screen w-screen bg-gradient-to-r from-violet-600 to-indigo-600">
        <NavigationBar></NavigationBar>
        <section className="flex pt-12">
          <div className=" flex flex-col m-auto w-[600px] min-h-[700px] bg-slate-100 p-2 gap-2 rounded-lg shadow-md border-[0.5px] border-slate-900">
            <InputBox stylesTypes="shadow-in">
              <GroupTasks>
                <InputTasks
                  title="Nome"
                  description="Digite o nome da sua casa"
                  name="casa-input"
                ></InputTasks>
                <InputTasks
                  title="Casa"
                  description="Digite o nome da sua casa"
                  name="casa-input"
                ></InputTasks>
              </GroupTasks>
              <InputTasks
                title="Casa"
                description="Digite o nome da sua casa"
                name="casa-input"
              ></InputTasks>
            </InputBox>

            <TasksList>
              <Tasks
                title="Lorem ipsum dolor sit amet consectetur adipisicing elit. Libero
                labore cumque perferendis voluptatem ipsa. Cupiditate hic culpa
                corporis id repellendus architecto non nobis quibusdam rerum
                maxime, eaque, iusto, commodi quasi.
                Lorem ipsum dolor sit amet consectetur adipisicing elit. Libero
                labore cumque perferendis voluptatem ipsa. Cupiditate hic culpa
                corporis id repellendus architecto non nobis quibusdam rerum
                maxime, eaque, iusto, commodi quasi.Lorem ipsum dolor sit amet consectetur adipisicing elit. Libero
                labore cumque perferendis voluptatem ipsa. Cupiditate hic culpa
                corporis id repellendus architecto non nobis quibusdam rerum
                maxime, eaque, iusto, commodi quasi.
                Lorem ipsum dolor sit amet consectetur adipisicing elit. Libero
                labore cumque perferendis voluptatem ipsa. Cupiditate hic culpa
                corporis id repellendus architecto non nobis quibusdam rerum
                maxime, eaque, iusto, commodi quasi.
                "
              ></Tasks>
              <Tasks title="Comprar Pão"></Tasks>
            </TasksList>
          </div>
        </section>
      </main>
    </>
  );
}

export default App;
