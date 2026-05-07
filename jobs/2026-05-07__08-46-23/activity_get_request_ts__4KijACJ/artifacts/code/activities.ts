import axios from 'axios';

export async function fetchData(): Promise<any> {
  const response = await axios.get('https://jsonplaceholder.typicode.com/todos/1');
  return response.data;
}
