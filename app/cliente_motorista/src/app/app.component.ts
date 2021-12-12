import { HttpClient } from '@angular/common/http';
import {Component, Inject} from '@angular/core';
import {MatDialog, MatDialogConfig} from '@angular/material/dialog';
import {MatSnackBar} from '@angular/material/snack-bar';
@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})

export class AppComponent {
  title = 'ClienteMotorista';
  serverData: any
  nome: any;
  telefone:any;
  IdUser: any;
  viagensDoUsuario:any = 0;
  idCorrida: any;
  listadeViagens:any = 0;
  eventSource:any;
  interesseRegistrado:any = 0;
  page:any = 1;
  aviso:any;
  URL: any;
  countUser:any;
  passageiroInfo:any = [];
  constructor(private httpClient: HttpClient, public dialog: MatDialog, private _snackBar: MatSnackBar) {
  }

  openSnackBar(message:any, action:any) {
    this._snackBar.open(message,action);
  }

  ngOnInit() {
    this.httpClient.get('http://127.0.0.1:5002/servidor/tamanho/lista/'+ '1').subscribe(data => {
      this.countUser = data as JSON;
      console.log(this.countUser);
      this.eventSource = new EventSource("http://127.0.0.1:5002/stream?channel=" + String(this.countUser) + '1')
      this.eventSource.addEventListener('publish',  (passageiroInfo:any)=>{
          data = String(data).replace("/", "" )
          this.passageiroInfo = String(passageiroInfo.data).replace("/", "" )
          this.openSnackBar("Encontramos uma viagem compátivel com a sua, para ver, clique na notificação", "Ok")
      },  true)
    })
   }

   mostrarViagemCompativel(){
    if(this.page == 4){
      this.page = 2;
     }else{
      this.page = 4;
     }
     var nome = this.passageiroInfo.toString().substring(this.passageiroInfo.indexOf('\"'), this.passageiroInfo.indexOf('\",'))
     var contato = this.passageiroInfo.toString().substring(this.passageiroInfo.indexOf('\",'), this.passageiroInfo.indexOf('\"]'))
     nome = String(nome).replace('\"', "" )
     contato = String(contato).replace('\"', "" )
     this.passageiroInfo = [nome, contato]
   }

  cadastro(nome:any, telefone:any) {
    this.nome = nome;
    this.telefone = telefone;
    this.page = 2;
    this.httpClient.post('http://127.0.0.1:5002/servidor/cadastro/' + nome + '/'+ telefone + '/1', "").subscribe(data => {
      this.IdUser = data as JSON;
      console.log(this.IdUser);
    })
  }

  minhasViagens() {
    this.httpClient.get('http://127.0.0.1:5002/servidor/consulta/viagens/' + this.IdUser  + '/1').subscribe(data => {
      this.viagensDoUsuario = data as JSON;
      console.log(this.viagensDoUsuario);
    })
  }

  consultaViagens(origem:any, destino:any, data:any) {
    data = String(data).replace("/", "" )
    data = String(data).replace("/", "" )
    this.httpClient.get('http://127.0.0.1:5002/servidor/consulta/' + origem + '/'+ destino + '/'+ data + '/1').subscribe(data => {
      this.listadeViagens = data as JSON;
      console.log(this.listadeViagens);
    })
  }

  interesseEmPassageira(origem:any, destino:any, data:any) {
    data = String(data).replace("/", "" )
    data = String(data).replace("/", "" )
    if(this.IdUser){
      this.httpClient.post('http://127.0.0.1:5002/servidor/interesse/passageira/' + this.IdUser + '/' + origem + '/'+ destino + '/'+ data , "").subscribe(response => {
        this.idCorrida = response  as JSON;
        console.log(this.idCorrida);
        this.minhasViagens()
      })
    }
  }

  removeInteresseEmPassageira(idCorrida:any) {
    this.httpClient.delete('http://127.0.0.1:5002/servidor/remove/interesse/passageira/' + idCorrida).subscribe(data => {
      this.listadeViagens = data as JSON;
      console.log(this.listadeViagens)
      this.minhasViagens()
    })
  }
}
